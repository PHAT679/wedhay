import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import { mockUsers, mockFacilities, mockEquipment } from '../../frontend/src/data/mockData';

// Only add missing reference data. Never erase events or reset existing passwords.
const prisma = new PrismaClient();
async function main() {
  const passwordHash = await bcrypt.hash('123456', 10);
  for (const user of mockUsers) {
    await prisma.user.upsert({ where: { email: user.email }, update: {}, create: {
      id: user.id, email: user.email, fullName: user.fullName, role: user.role,
      department: user.department, phone: user.phone, passwordHash,
    } });
  }
  for (const f of mockFacilities) {
    await prisma.facility.upsert({ where: { code: f.code }, update: {}, create: {
      id: f.id, code: f.code, name: f.name, location: f.location, capacity: f.capacity,
      type: f.type, description: f.description, amenities: JSON.stringify(f.amenities),
    } });
  }
  for (const e of mockEquipment) {
    await prisma.equipment.upsert({ where: { code: e.code }, update: {}, create: {
      id: e.id, code: e.code, name: e.name, type: e.type, totalQuantity: e.totalQuantity, condition: e.condition,
    } });
  }
  console.log('Reference data ready. Existing events and accounts were preserved.');
}
main().catch(error => { console.error(error); process.exitCode = 1; }).finally(() => prisma.$disconnect());
