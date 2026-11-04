const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const backendDir = path.resolve(__dirname, '..');
const database = path.resolve(backendDir, `prisma/event-workflow-test-${process.pid}-${Date.now()}.db`);
process.env.DATABASE_URL = `file:${database.replace(/\\/g, '/')}`;
process.env.JWT_SECRET = require('node:crypto').randomBytes(32).toString('hex');

let server;
let prisma;

async function main() {
  const schema = spawnSync(process.execPath, [
    'node_modules/prisma/build/index.js',
    'db',
    'push',
    '--schema',
    'prisma/schema.prisma',
    '--skip-generate',
  ], { cwd: backendDir, env: process.env, encoding: 'utf8' });
  if (schema.status !== 0) throw new Error(schema.stderr || schema.stdout);

  prisma = require('../dist/config/database').default;
  const bcrypt = require('bcryptjs');
  const app = require('../dist/app').default;
  const hash = await bcrypt.hash('test-password', 4);

  for (const [id, role] of [
    ['btc-test', 'BTC'],
    ['bcn-test', 'BCN_KHOA'],
    ['other-btc-test', 'BTC'],
    ['admin-test', 'ADMIN'],
  ]) {
    await prisma.user.create({
      data: {
        id,
        email: `${id}@test.example`,
        fullName: id,
        role,
        passwordHash: hash,
        department: 'Test',
      },
    });
  }

  const authService = require('../dist/services/auth.service');
  const legacyEmail = 'legacy-pending@test.example';
  const legacyUser = await prisma.user.create({
    data: {
      id: 'legacy-pending',
      email: legacyEmail,
      fullName: 'Legacy Pending',
      role: 'BTC',
      passwordHash: 'not-a-bcrypt-hash',
      isActive: false,
    },
  });
  await prisma.legacyIdentityMap.create({
    data: {
      entity: 'User',
      legacyId: BigInt(987654321),
      applicationId: legacyUser.id,
    },
  });
  await prisma.legacyIdentityMap.create({
    data: {
      entity: 'UserActivation',
      legacyId: BigInt(987654321),
      applicationId: legacyUser.id,
    },
  });
  await assert.rejects(() => authService.login(legacyEmail, '123456'), /đã bị khóa/);

  let activationOtp;
  await authService.requestPasswordReset(legacyEmail, async (_email, otp) => {
    activationOtp = otp;
    return { sent: true };
  });
  const pendingToken = await prisma.passwordResetToken.findFirst({
    where: { email: legacyEmail },
    orderBy: { createdAt: 'desc' },
  });
  assert.ok(pendingToken);
  assert.notEqual(pendingToken.token, activationOtp, 'neither OTP nor session token is stored in plaintext');
  assert.ok(await bcrypt.compare(activationOtp, pendingToken.otpHash));
  assert.equal((await prisma.legacyIdentityMap.findUnique({
    where: { entity_legacyId: { entity: 'UserActivation', legacyId: BigInt(987654321) } },
  })).verifiedAt, null);

  const verifiedOtp = await authService.verifyResetOtp(legacyEmail, activationOtp);
  assert.notEqual(pendingToken.token, verifiedOtp.resetSessionToken);
  const verifiedToken = await prisma.passwordResetToken.findUnique({ where: { id: pendingToken.id } });
  assert.equal(
    verifiedToken.token,
    require('node:crypto').createHash('sha256').update(verifiedOtp.resetSessionToken).digest('hex'),
  );
  assert.equal((await authService.verifyResetToken(verifiedOtp.resetSessionToken)).valid, true);

  await authService.resetPassword(verifiedOtp.resetSessionToken, 'new-legacy-password');
  const activatedUser = await prisma.user.findUnique({ where: { id: legacyUser.id } });
  assert.equal(activatedUser.isActive, true, 'legacy account activates only after OTP-verified password setup');
  assert.equal(
    (await prisma.legacyIdentityMap.findUnique({
      where: { entity_legacyId: { entity: 'UserActivation', legacyId: BigInt(987654321) } },
    })).verifiedAt instanceof Date,
    true,
  );
  await assert.rejects(() => authService.login(legacyEmail, '123456'), /Email hoặc mật khẩu không đúng/);
  assert.equal((await authService.login(legacyEmail, 'new-legacy-password')).user.role, 'BTC');
  await assert.rejects(() => authService.resetPassword(verifiedOtp.resetSessionToken, 'another-password'));
  assert.equal((await authService.verifyResetToken(verifiedOtp.resetSessionToken)).valid, false);

  const inactiveWithoutMap = await prisma.user.create({
    data: {
      id: 'inactive-without-map',
      email: 'inactive-without-map@test.example',
      fullName: 'Inactive Without Map',
      role: 'BTC',
      passwordHash: 'not-a-bcrypt-hash',
      isActive: false,
    },
  });
  await prisma.legacyIdentityMap.create({
    data: {
      entity: 'User',
      legacyId: BigInt(987654323),
      applicationId: inactiveWithoutMap.id,
    },
  });
  let ineligibleEmailSent = false;
  await authService.requestPasswordReset(inactiveWithoutMap.email, async () => {
    ineligibleEmailSent = true;
    return { sent: true };
  });
  assert.equal(ineligibleEmailSent, false, 'ordinary administratively disabled accounts cannot self-activate');

  const failedDeliveryEmail = 'legacy-mail-failure@test.example';
  const failedDeliveryUser = await prisma.user.create({
    data: {
      id: 'legacy-mail-failure',
      email: failedDeliveryEmail,
      fullName: 'Legacy Mail Failure',
      role: 'BTC',
      passwordHash: 'unusable-imported-secret',
      isActive: false,
    },
  });
  await prisma.legacyIdentityMap.create({
    data: {
      entity: 'User',
      legacyId: BigInt(987654322),
      applicationId: failedDeliveryUser.id,
    },
  });
  await prisma.legacyIdentityMap.create({
    data: {
      entity: 'UserActivation',
      legacyId: BigInt(987654322),
      applicationId: failedDeliveryUser.id,
    },
  });
  await authService.requestPasswordReset(failedDeliveryEmail, async () => ({
    sent: false,
    reason: 'SMTP_SEND_FAILED',
  }));
  assert.equal(
    (await prisma.passwordResetToken.findFirst({
      where: { email: failedDeliveryEmail },
      orderBy: { createdAt: 'desc' },
    })).used,
    true,
    'a failed delivery invalidates the OTP',
  );

  await prisma.facility.create({
    data: { id: 'hall-test', code: 'HALL-TEST', name: 'Test Hall', type: 'HALL', capacity: 500 },
  });
  await prisma.equipment.create({
    data: { id: 'projector-test', code: 'PROJECTOR-TEST', name: 'Test Projector', type: 'PROJECTOR', totalQuantity: 3 },
  });

  server = app.listen(0, '127.0.0.1');
  await new Promise((resolve) => server.once('listening', resolve));
  const base = `http://127.0.0.1:${server.address().port}/api`;

  async function call(url, token, method = 'GET', body, idempotencyKey) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;
    if (idempotencyKey) headers['Idempotency-Key'] = idempotencyKey;
    const response = await fetch(base + url, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    return { status: response.status, body: await response.json() };
  }

  assert.equal((await call('/events')).status, 401, 'event API requires authentication');

  // Use a nonexistent email for the negative-auth case so the test never increments a real test user's lockout counter.
  const invalidLogin = await call('/auth/login', null, 'POST', {
    email: 'not-seeded@test.example',
    password: 'bad-password',
  });
  assert.equal(invalidLogin.status, 401);

  async function login(id) {
    const response = await call('/auth/login', null, 'POST', {
      email: `${id}@test.example`,
      password: 'test-password',
    });
    assert.equal(response.status, 200, JSON.stringify(response.body));
    return response.body.data.token;
  }

  const btc = await login('btc-test');
  const bcn = await login('bcn-test');
  await login('other-btc-test');
  const admin = await login('admin-test');
  assert.equal((await prisma.user.findUnique({ where: { id: 'btc-test' } })).failedLoginAttempts, 0);

  const missingInitialPassword = await call('/users', admin, 'POST', {
    email: 'admin-created-without-password@test.example',
    fullName: 'No Default Password',
    role: 'BTC',
  });
  assert.equal(missingInitialPassword.status, 400);
  assert.equal(
    await prisma.user.findUnique({ where: { email: 'admin-created-without-password@test.example' } }),
    null,
    'admin account creation must not fall back to a shared password',
  );

  const eventCountBeforeInvalidBooking = await prisma.event.count();
  const emptyResourceIds = await call('/events', btc, 'POST', {
    title: 'Invalid resource IDs',
    organizingUnit: 'Test',
    booking: {
      facilityId: '',
      startTime: '2030-01-02T08:00:00.000Z',
      endTime: '2030-01-02T11:00:00.000Z',
      equipmentItems: [{ equipmentId: '', quantity: 1 }],
    },
  });
  assert.equal(emptyResourceIds.status, 400);
  assert.ok(emptyResourceIds.body.data.some((issue) => issue.field === 'booking.facilityId'));
  assert.ok(emptyResourceIds.body.data.some((issue) => issue.field === 'booking.equipmentItems.0.equipmentId'));
  assert.equal(await prisma.event.count(), eventCountBeforeInvalidBooking, 'invalid empty IDs must not persist an event');

  const idempotencyKey = require('node:crypto').randomUUID();
  const draftPayload = { title: 'Event workflow integration test', organizingUnit: 'Test BTC' };
  const createdDraft = await call('/events', btc, 'POST', draftPayload, idempotencyKey);
  assert.equal(createdDraft.status, 201, JSON.stringify(createdDraft.body));
  const eventId = createdDraft.body.data.id;
  assert.equal(createdDraft.body.data.status, 'DRAFT');
  assert.equal(createdDraft.body.data.resourceBookings.length, 0, 'a draft without a selected venue has no booking');
  assert.ok(await prisma.event.findUnique({ where: { id: eventId } }), '201 is returned only after the event was committed');

  const retry = await call('/events', btc, 'POST', draftPayload, idempotencyKey);
  assert.equal(retry.status, 201);
  assert.equal(retry.body.data.id, eventId, 'retries return the original persisted event');
  assert.equal(await prisma.event.count(), eventCountBeforeInvalidBooking + 1, 'idempotent retry must not duplicate events');

  const changedRetry = await call('/events', btc, 'POST', {
    ...draftPayload,
    title: 'Changed payload',
  }, idempotencyKey);
  assert.equal(changedRetry.status, 409, 'an idempotency key cannot be reused for a different payload');

  const rejectedIncompleteSubmission = await call(`/events/${eventId}/submit`, btc, 'POST');
  assert.equal(rejectedIncompleteSubmission.status, 422);
  assert.ok(rejectedIncompleteSubmission.body.data.some((issue) => issue.field === 'objectives'));
  assert.equal((await prisma.event.findUnique({ where: { id: eventId } })).status, 'DRAFT');

  const completedDraft = await call(`/events/${eventId}`, btc, 'PUT', {
    objectives: 'Run a student academic workshop',
    expectedAttendees: 40,
    startDate: '2030-01-02T08:00:00.000Z',
    endDate: '2030-01-02T11:00:00.000Z',
    scheduleItems: [{ timeSlot: '08:00-09:00', activity: 'Opening session' }],
    booking: {
      facilityId: 'hall-test',
      startTime: '2030-01-02T08:00:00.000Z',
      endTime: '2030-01-02T11:00:00.000Z',
      equipmentItems: [{ equipmentId: 'projector-test', quantity: 2 }],
    },
    expectedVersion: 1,
  });
  assert.equal(completedDraft.status, 200, JSON.stringify(completedDraft.body));
  assert.equal(completedDraft.body.data.title, draftPayload.title);
  assert.equal(completedDraft.body.data.resourceBookings.length, 1);
  assert.equal(completedDraft.body.data.resourceBookings[0].facilityId, 'hall-test');
  assert.deepEqual(completedDraft.body.data.resourceBookings[0].bookingItems.map((item) => ({
    equipmentId: item.equipmentId,
    quantity: item.quantity,
  })), [{ equipmentId: 'projector-test', quantity: 2 }]);
  assert.equal(await prisma.resourceBooking.count({ where: { eventId } }), 1);
  assert.equal(await prisma.resourceBookingItem.count({ where: { booking: { eventId } } }), 1);

  const submitted = await call(`/events/${eventId}/submit`, btc, 'POST');
  assert.equal(submitted.status, 200, JSON.stringify(submitted.body));
  assert.equal(submitted.body.data.status, 'FACULTY_REVIEW');
  const persistedSubmission = await prisma.event.findUnique({ where: { id: eventId } });
  assert.equal(persistedSubmission.status, 'FACULTY_REVIEW');
  const history = await prisma.workflowHistory.findMany({ where: { eventId }, orderBy: { createdAt: 'asc' } });
  assert.deepEqual(history.map((entry) => entry.action), ['CREATE', 'UPDATE', 'SUBMIT']);

  const duplicateSubmit = await call(`/events/${eventId}/submit`, btc, 'POST');
  assert.equal(duplicateSubmit.status, 200);
  assert.equal(await prisma.workflowHistory.count({ where: { eventId, action: 'SUBMIT' } }), 1);

  const bcnList = await call('/events?page=1&limit=100', bcn);
  assert.equal(bcnList.status, 200);
  assert.ok(bcnList.body.events.some((event) => event.id === eventId), 'BCN Khoa can see the submitted event');
  const bcnActions = await call(`/events/${eventId}/available-actions`, bcn);
  assert.equal(bcnActions.status, 200);
  assert.ok(bcnActions.body.data.includes('APPROVE'), 'BCN Khoa has the existing approval action');
  const btcActions = await call(`/events/${eventId}/available-actions`, btc);
  assert.equal(btcActions.status, 200);
  assert.ok(!btcActions.body.data.includes('APPROVE'), 'BTC does not gain BCN Khoa approval authority');
  assert.ok(await prisma.notification.count({ where: { userId: 'bcn-test', eventId, category: 'APPROVAL' } }));

  const noEquipmentDraft = await call('/events', btc, 'POST', {
    title: 'Event without optional equipment',
    organizingUnit: 'Test BTC',
  });
  assert.equal(noEquipmentDraft.status, 201);
  const noEquipmentId = noEquipmentDraft.body.data.id;
  const noEquipmentUpdate = await call(`/events/${noEquipmentId}`, btc, 'PUT', {
    objectives: 'Run an event without optional equipment',
    expectedAttendees: 20,
    startDate: '2030-01-03T08:00:00.000Z',
    endDate: '2030-01-03T11:00:00.000Z',
    scheduleItems: [{ timeSlot: '08:00-09:00', activity: 'Opening session' }],
    booking: {
      facilityId: 'hall-test',
      startTime: '2030-01-03T08:00:00.000Z',
      endTime: '2030-01-03T11:00:00.000Z',
      equipmentItems: [],
    },
    expectedVersion: 1,
  });
  assert.equal(noEquipmentUpdate.status, 200, JSON.stringify(noEquipmentUpdate.body));
  assert.equal(noEquipmentUpdate.body.data.resourceBookings[0].bookingItems.length, 0);
  assert.equal((await call(`/events/${noEquipmentId}/submit`, btc, 'POST')).status, 200);
  assert.equal((await prisma.event.findUnique({ where: { id: noEquipmentId } })).status, 'FACULTY_REVIEW');

  console.log('PASS: isolated draft/create/update/booking/optional-equipment/submit/idempotency/history/BCN visibility and role-action checks.');
}

main()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(async () => {
    if (server) await new Promise((resolve) => server.close(resolve));
    if (prisma) await prisma.$disconnect();
    if (fs.existsSync(database)) fs.unlinkSync(database);
  });
