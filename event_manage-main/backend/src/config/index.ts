import dotenv from 'dotenv';
dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3001', 10),
  jwtSecret: process.env.JWT_SECRET || 'eventflow-dev-secret',
  corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  uploadDir: process.env.UPLOAD_DIR || './uploads',
  maxFileSize: parseInt(process.env.MAX_FILE_SIZE || '10485760', 10),
  aiApiKey: process.env.AI_API_KEY || '',
  aiProvider: process.env.AI_PROVIDER || 'rule-based',
  jwtExpiresIn: '24h',
};
