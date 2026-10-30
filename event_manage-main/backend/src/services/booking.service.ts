import prisma from '../config/database';

export async function checkAvailability(facilityId: string, startTime: Date, endTime: Date, excludeBookingId?: string) {
  const where: Record<string, unknown> = {
    facilityId,
    status: { in: ['PENDING', 'TENTATIVE', 'CONFIRMED'] },
    // Overlap check: NOT(end1 <= start2 OR start1 >= end2) => start1 < end2 AND end1 > start2
    startTime: { lt: endTime },
    endTime: { gt: startTime },
  };

  if (excludeBookingId) {
    where.id = { not: excludeBookingId };
  }

  const conflicts = await prisma.resourceBooking.findMany({
    where,
    include: {
      facility: true,
      event: { select: { id: true, eventCode: true, title: true } },
    },
  });

  return conflicts;
}

export async function checkEquipmentAvailability(
  equipmentId: string,
  quantity: number,
  startTime: Date,
  endTime: Date,
  excludeBookingId?: string
) {
  const equipment = await prisma.equipment.findUnique({ where: { id: equipmentId } });
  if (!equipment) throw new Error('Không tìm thấy thiết bị');

  const where: Record<string, unknown> = {
    equipmentId,
    booking: {
      status: { in: ['PENDING', 'TENTATIVE', 'CONFIRMED'] },
      startTime: { lt: endTime },
      endTime: { gt: startTime },
    },
  };

  if (excludeBookingId) {
    where.booking = {
      ...(where.booking as Record<string, unknown>),
      id: { not: excludeBookingId },
    };
  }

  const bookedItems = await prisma.resourceBookingItem.findMany({ where });
  const totalBooked = bookedItems.reduce((sum, item) => sum + item.quantity, 0);
  const available = equipment.totalQuantity - totalBooked;

  return {
    equipment,
    totalQuantity: equipment.totalQuantity,
    booked: totalBooked,
    available,
    isAvailable: available >= quantity,
  };
}

export async function createBooking(data: {
  eventId: string;
  facilityId: string;
  startTime: string;
  endTime: string;
  setupTime?: string;
  teardownTime?: string;
  expectedAttendees?: number;
  purpose?: string;
  specialRequests?: string;
  alternativeOption?: string;
  equipmentItems?: Array<{ equipmentId: string; quantity: number }>;
}) {
  const start = new Date(data.startTime);
  const end = new Date(data.endTime);

  // Check facility availability
  const conflicts = await checkAvailability(data.facilityId, start, end);
  if (conflicts.length > 0) {
    const conflictInfo = conflicts.map(c =>
      `${c.event.eventCode} (${c.startTime.toLocaleString()} - ${c.endTime.toLocaleString()})`
    ).join(', ');
    throw new Error(`Phòng đã được đặt trong khoảng thời gian này. Xung đột với: ${conflictInfo}`);
  }

  // Check facility capacity
  const facility = await prisma.facility.findUnique({ where: { id: data.facilityId } });
  if (facility && data.expectedAttendees && facility.capacity && data.expectedAttendees > facility.capacity) {
    throw new Error(`Số người tham dự (${data.expectedAttendees}) vượt quá sức chứa phòng (${facility.capacity})`);
  }

  // Check equipment availability
  if (data.equipmentItems?.length) {
    for (const item of data.equipmentItems) {
      const check = await checkEquipmentAvailability(item.equipmentId, item.quantity, start, end);
      if (!check.isAvailable) {
        throw new Error(`Thiết bị "${check.equipment.name}" không đủ số lượng (cần ${item.quantity}, khả dụng ${check.available})`);
      }
    }
  }

  const booking = await prisma.$transaction(async (tx) => {
    const created = await tx.resourceBooking.create({
      data: {
        eventId: data.eventId,
        facilityId: data.facilityId,
        startTime: start,
        endTime: end,
        setupTime: data.setupTime ? new Date(data.setupTime) : undefined,
        teardownTime: data.teardownTime ? new Date(data.teardownTime) : undefined,
        expectedAttendees: data.expectedAttendees,
        purpose: data.purpose,
        specialRequests: data.specialRequests,
        alternativeOption: data.alternativeOption,
        status: 'PENDING',
      },
    });

    if (data.equipmentItems?.length) {
      await tx.resourceBookingItem.createMany({
        data: data.equipmentItems.map((item) => ({
          bookingId: created.id,
          equipmentId: item.equipmentId,
          quantity: item.quantity,
        })),
      });
    }

    return created;
  });

  return booking;
}

export async function confirmBooking(bookingId: string, userId: string) {
  const booking = await prisma.resourceBooking.findUnique({ where: { id: bookingId } });
  if (!booking) throw new Error('Không tìm thấy đặt chỗ');
  if (booking.status !== 'PENDING' && booking.status !== 'TENTATIVE') {
    throw new Error('Không thể xác nhận đặt chỗ ở trạng thái hiện tại');
  }

  // Re-check availability at confirmation time (prevent race condition)
  const conflicts = await checkAvailability(booking.facilityId, booking.startTime, booking.endTime, bookingId);
  if (conflicts.length > 0) {
    throw new Error('Phòng đã được đặt bởi sự kiện khác trong khoảng thời gian này');
  }

  return prisma.resourceBooking.update({
    where: { id: bookingId },
    data: { status: 'CONFIRMED', confirmedById: userId, confirmedAt: new Date() },
  });
}

export async function rejectBooking(bookingId: string, userId: string) {
  return prisma.resourceBooking.update({
    where: { id: bookingId },
    data: { status: 'REJECTED' },
  });
}

export async function getBookingsForFacility(facilityId: string, startDate: Date, endDate: Date) {
  return prisma.resourceBooking.findMany({
    where: {
      facilityId,
      status: { in: ['PENDING', 'TENTATIVE', 'CONFIRMED'] },
      startTime: { lt: endDate },
      endTime: { gt: startDate },
    },
    include: {
      event: { select: { id: true, eventCode: true, title: true, organizingUnit: true } },
      facility: true,
      bookingItems: { include: { equipment: true } },
    },
    orderBy: { startTime: 'asc' },
  });
}

export async function getAllBookings(filters?: { status?: string; eventId?: string }) {
  const where: Record<string, unknown> = {};
  if (filters?.status) where.status = filters.status;
  if (filters?.eventId) where.eventId = filters.eventId;

  return prisma.resourceBooking.findMany({
    where,
    include: {
      event: { select: { id: true, eventCode: true, title: true } },
      facility: true,
      bookingItems: { include: { equipment: true } },
    },
    orderBy: { startTime: 'desc' },
  });
}
