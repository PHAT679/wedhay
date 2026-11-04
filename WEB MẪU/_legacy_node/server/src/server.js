import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { initDatabase } from './database.js';

import authRoutes from './routes/auth.js';
import serviceRoutes from './routes/services.js';
import appointmentRoutes from './routes/appointments.js';
import assignmentRoutes from './routes/assignments.js';
import customerRoutes from './routes/customers.js';
import paymentRoutes from './routes/payments.js';
import notificationRoutes from './routes/notifications.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Khởi tạo Database và Seed Data
initDatabase();

// Đăng ký API Routes
app.use('/api/auth', authRoutes);
app.use('/api/services', serviceRoutes);
app.use('/api/appointments', appointmentRoutes);
app.use('/api/assignments', assignmentRoutes);
app.use('/api/customers', customerRoutes);
app.use('/api/payments', paymentRoutes);
app.use('/api/notifications', notificationRoutes);

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    system: 'Emmay Beauty Appointment Management System API',
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(`🌸 Emmay Beauty Backend Server running on port ${PORT}`);
  console.log(`🌸 API Health Check: http://localhost:${PORT}/api/health`);
  console.log(`====================================================`);
});
