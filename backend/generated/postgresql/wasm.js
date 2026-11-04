
Object.defineProperty(exports, "__esModule", { value: true });

const {
  Decimal,
  objectEnumValues,
  makeStrictEnum,
  Public,
  getRuntime,
  skip
} = require('./runtime/index-browser.js')


const Prisma = {}

exports.Prisma = Prisma
exports.$Enums = {}

/**
 * Prisma Client JS version: 5.22.0
 * Query Engine version: 605197351a3c8bdd595af2d2a9bc3025bca48ea2
 */
Prisma.prismaVersion = {
  client: "5.22.0",
  engine: "605197351a3c8bdd595af2d2a9bc3025bca48ea2"
}

Prisma.PrismaClientKnownRequestError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientKnownRequestError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)};
Prisma.PrismaClientUnknownRequestError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientUnknownRequestError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientRustPanicError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientRustPanicError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientInitializationError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientInitializationError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientValidationError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientValidationError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.NotFoundError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`NotFoundError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.Decimal = Decimal

/**
 * Re-export of sql-template-tag
 */
Prisma.sql = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`sqltag is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.empty = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`empty is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.join = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`join is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.raw = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`raw is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.validator = Public.validator

/**
* Extensions
*/
Prisma.getExtensionContext = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`Extensions.getExtensionContext is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.defineExtension = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`Extensions.defineExtension is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}

/**
 * Shorthand utilities for JSON filtering
 */
Prisma.DbNull = objectEnumValues.instances.DbNull
Prisma.JsonNull = objectEnumValues.instances.JsonNull
Prisma.AnyNull = objectEnumValues.instances.AnyNull

Prisma.NullTypes = {
  DbNull: objectEnumValues.classes.DbNull,
  JsonNull: objectEnumValues.classes.JsonNull,
  AnyNull: objectEnumValues.classes.AnyNull
}



/**
 * Enums
 */

exports.Prisma.TransactionIsolationLevel = makeStrictEnum({
  ReadUncommitted: 'ReadUncommitted',
  ReadCommitted: 'ReadCommitted',
  RepeatableRead: 'RepeatableRead',
  Serializable: 'Serializable'
});

exports.Prisma.UserScalarFieldEnum = {
  id: 'id',
  email: 'email',
  passwordHash: 'passwordHash',
  fullName: 'fullName',
  phone: 'phone',
  role: 'role',
  department: 'department',
  isActive: 'isActive',
  failedLoginAttempts: 'failedLoginAttempts',
  lockedUntil: 'lockedUntil',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.EventScalarFieldEnum = {
  id: 'id',
  eventCode: 'eventCode',
  title: 'title',
  description: 'description',
  objectives: 'objectives',
  targetAudience: 'targetAudience',
  expectedAttendees: 'expectedAttendees',
  organizingUnit: 'organizingUnit',
  contactPerson: 'contactPerson',
  contactEmail: 'contactEmail',
  contactPhone: 'contactPhone',
  startDate: 'startDate',
  endDate: 'endDate',
  setupTime: 'setupTime',
  teardownTime: 'teardownTime',
  preferredVenue: 'preferredVenue',
  planContent: 'planContent',
  safetyPlan: 'safetyPlan',
  communicationPlan: 'communicationPlan',
  status: 'status',
  permitStatus: 'permitStatus',
  facilityStatus: 'facilityStatus',
  inspectionStatus: 'inspectionStatus',
  settlementStatus: 'settlementStatus',
  reportStatus: 'reportStatus',
  currentVersion: 'currentVersion',
  createdById: 'createdById',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt',
  deletedAt: 'deletedAt'
};

exports.Prisma.EventVersionScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  version: 'version',
  title: 'title',
  description: 'description',
  objectives: 'objectives',
  planContent: 'planContent',
  budgetData: 'budgetData',
  changeNote: 'changeNote',
  changedBy: 'changedBy',
  isActive: 'isActive',
  createdAt: 'createdAt'
};

exports.Prisma.EventScheduleItemScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  timeSlot: 'timeSlot',
  activity: 'activity',
  responsible: 'responsible',
  notes: 'notes',
  sortOrder: 'sortOrder',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.BudgetItemScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  category: 'category',
  itemName: 'itemName',
  quantity: 'quantity',
  unitPrice: 'unitPrice',
  totalPrice: 'totalPrice',
  notes: 'notes',
  actualQuantity: 'actualQuantity',
  actualPrice: 'actualPrice',
  actualTotal: 'actualTotal',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ApprovalDecisionScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  stage: 'stage',
  decision: 'decision',
  comments: 'comments',
  reason: 'reason',
  version: 'version',
  decidedById: 'decidedById',
  createdAt: 'createdAt'
};

exports.Prisma.WorkflowHistoryScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  fromStatus: 'fromStatus',
  toStatus: 'toStatus',
  action: 'action',
  actorId: 'actorId',
  actorName: 'actorName',
  actorRole: 'actorRole',
  comments: 'comments',
  metadata: 'metadata',
  createdAt: 'createdAt'
};

exports.Prisma.AttachmentScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  fileName: 'fileName',
  originalName: 'originalName',
  fileType: 'fileType',
  fileSize: 'fileSize',
  filePath: 'filePath',
  category: 'category',
  uploadedById: 'uploadedById',
  createdAt: 'createdAt'
};

exports.Prisma.FacilityScalarFieldEnum = {
  id: 'id',
  code: 'code',
  name: 'name',
  location: 'location',
  capacity: 'capacity',
  type: 'type',
  description: 'description',
  amenities: 'amenities',
  isActive: 'isActive',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.EquipmentScalarFieldEnum = {
  id: 'id',
  code: 'code',
  name: 'name',
  type: 'type',
  totalQuantity: 'totalQuantity',
  description: 'description',
  condition: 'condition',
  isActive: 'isActive',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ResourceBookingScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  facilityId: 'facilityId',
  startTime: 'startTime',
  endTime: 'endTime',
  setupTime: 'setupTime',
  teardownTime: 'teardownTime',
  expectedAttendees: 'expectedAttendees',
  purpose: 'purpose',
  specialRequests: 'specialRequests',
  alternativeOption: 'alternativeOption',
  status: 'status',
  confirmedById: 'confirmedById',
  confirmedAt: 'confirmedAt',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ResourceBookingItemScalarFieldEnum = {
  id: 'id',
  bookingId: 'bookingId',
  equipmentId: 'equipmentId',
  quantity: 'quantity',
  createdAt: 'createdAt'
};

exports.Prisma.HandoverRecordScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  type: 'type',
  handoverById: 'handoverById',
  receivedById: 'receivedById',
  facilityCondition: 'facilityCondition',
  equipmentList: 'equipmentList',
  notes: 'notes',
  status: 'status',
  handoverDate: 'handoverDate',
  confirmedAt: 'confirmedAt',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ReturnInspectionScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  inspectedById: 'inspectedById',
  facilityCondition: 'facilityCondition',
  equipmentCondition: 'equipmentCondition',
  overallResult: 'overallResult',
  notes: 'notes',
  inspectedAt: 'inspectedAt',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.IncidentReportScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  reportedById: 'reportedById',
  type: 'type',
  description: 'description',
  severity: 'severity',
  resolution: 'resolution',
  status: 'status',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.SettlementScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  totalBudgeted: 'totalBudgeted',
  totalActual: 'totalActual',
  difference: 'difference',
  status: 'status',
  submittedById: 'submittedById',
  submittedAt: 'submittedAt',
  reviewedById: 'reviewedById',
  reviewedAt: 'reviewedAt',
  reviewNotes: 'reviewNotes',
  rejectionReason: 'rejectionReason',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.SettlementItemScalarFieldEnum = {
  id: 'id',
  settlementId: 'settlementId',
  itemName: 'itemName',
  category: 'category',
  budgetedAmount: 'budgetedAmount',
  actualAmount: 'actualAmount',
  difference: 'difference',
  notes: 'notes',
  createdAt: 'createdAt'
};

exports.Prisma.FinancialDocumentScalarFieldEnum = {
  id: 'id',
  settlementId: 'settlementId',
  documentType: 'documentType',
  documentNumber: 'documentNumber',
  amount: 'amount',
  description: 'description',
  fileName: 'fileName',
  filePath: 'filePath',
  isVerified: 'isVerified',
  verifiedAt: 'verifiedAt',
  createdAt: 'createdAt'
};

exports.Prisma.EventReportScalarFieldEnum = {
  id: 'id',
  eventId: 'eventId',
  actualAttendees: 'actualAttendees',
  summary: 'summary',
  achievements: 'achievements',
  challenges: 'challenges',
  lessonsLearned: 'lessonsLearned',
  recommendations: 'recommendations',
  status: 'status',
  submittedAt: 'submittedAt',
  acceptedAt: 'acceptedAt',
  acceptedBy: 'acceptedBy',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.NotificationScalarFieldEnum = {
  id: 'id',
  userId: 'userId',
  eventId: 'eventId',
  title: 'title',
  content: 'content',
  type: 'type',
  category: 'category',
  isRead: 'isRead',
  readAt: 'readAt',
  linkUrl: 'linkUrl',
  createdAt: 'createdAt'
};

exports.Prisma.AuditLogScalarFieldEnum = {
  id: 'id',
  userId: 'userId',
  action: 'action',
  entityType: 'entityType',
  entityId: 'entityId',
  oldValue: 'oldValue',
  newValue: 'newValue',
  ipAddress: 'ipAddress',
  userAgent: 'userAgent',
  createdAt: 'createdAt'
};

exports.Prisma.SystemSettingScalarFieldEnum = {
  id: 'id',
  key: 'key',
  value: 'value',
  description: 'description',
  category: 'category',
  updatedAt: 'updatedAt'
};

exports.Prisma.PasswordResetTokenScalarFieldEnum = {
  id: 'id',
  email: 'email',
  token: 'token',
  otpHash: 'otpHash',
  attempts: 'attempts',
  expiresAt: 'expiresAt',
  verified: 'verified',
  used: 'used',
  createdAt: 'createdAt'
};

exports.Prisma.LegacyIdentityMapScalarFieldEnum = {
  entity: 'entity',
  legacyId: 'legacyId',
  applicationId: 'applicationId',
  verifiedAt: 'verifiedAt'
};

exports.Prisma.SortOrder = {
  asc: 'asc',
  desc: 'desc'
};

exports.Prisma.QueryMode = {
  default: 'default',
  insensitive: 'insensitive'
};

exports.Prisma.NullsOrder = {
  first: 'first',
  last: 'last'
};


exports.Prisma.ModelName = {
  User: 'User',
  Event: 'Event',
  EventVersion: 'EventVersion',
  EventScheduleItem: 'EventScheduleItem',
  BudgetItem: 'BudgetItem',
  ApprovalDecision: 'ApprovalDecision',
  WorkflowHistory: 'WorkflowHistory',
  Attachment: 'Attachment',
  Facility: 'Facility',
  Equipment: 'Equipment',
  ResourceBooking: 'ResourceBooking',
  ResourceBookingItem: 'ResourceBookingItem',
  HandoverRecord: 'HandoverRecord',
  ReturnInspection: 'ReturnInspection',
  IncidentReport: 'IncidentReport',
  Settlement: 'Settlement',
  SettlementItem: 'SettlementItem',
  FinancialDocument: 'FinancialDocument',
  EventReport: 'EventReport',
  Notification: 'Notification',
  AuditLog: 'AuditLog',
  SystemSetting: 'SystemSetting',
  PasswordResetToken: 'PasswordResetToken',
  LegacyIdentityMap: 'LegacyIdentityMap'
};

/**
 * This is a stub Prisma Client that will error at runtime if called.
 */
class PrismaClient {
  constructor() {
    return new Proxy(this, {
      get(target, prop) {
        let message
        const runtime = getRuntime()
        if (runtime.isEdge) {
          message = `PrismaClient is not configured to run in ${runtime.prettyName}. In order to run Prisma Client on edge runtime, either:
- Use Prisma Accelerate: https://pris.ly/d/accelerate
- Use Driver Adapters: https://pris.ly/d/driver-adapters
`;
        } else {
          message = 'PrismaClient is unable to run in this browser environment, or has been bundled for the browser (running in `' + runtime.prettyName + '`).'
        }
        
        message += `
If this is unexpected, please open an issue: https://pris.ly/prisma-prisma-bug-report`

        throw new Error(message)
      }
    })
  }
}

exports.PrismaClient = PrismaClient

Object.assign(exports, Prisma)
