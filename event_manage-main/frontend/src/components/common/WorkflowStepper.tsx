import React from 'react';
import { Check, Clock, AlertTriangle, XCircle, FileText } from 'lucide-react';
import { EventStatus } from '../../types';
import { workflowStages, getCurrentStageIndex, statusLabels } from '../../utils/helpers';

interface WorkflowStepperProps {
  status: EventStatus;
}

export const WorkflowStepper: React.FC<WorkflowStepperProps> = ({ status }) => {
  const currentStageIndex = getCurrentStageIndex(status);
  const isRejected = status.includes('REJECTED');
  const isRevision = status.includes('REVISION');
  const isConflict = status === 'FACILITY_CONFLICT';

  return (
    <div className="w-full bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-500">
            Tiến trình Quy trình Tiếp nhận & Phê duyệt
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Giai đoạn hiện tại: <span className="font-semibold text-slate-700">{workflowStages[currentStageIndex]?.name}</span>
          </p>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${statusLabels[status]?.bg} ${statusLabels[status]?.color} ${statusLabels[status]?.border}`}>
          {statusLabels[status]?.label}
        </div>
      </div>

      {/* Responsive Horizontal Stepper */}
      <div className="overflow-x-auto pb-2">
        <div className="flex items-center min-w-[760px] justify-between relative">
          {/* Background Connecting Line */}
          <div className="absolute left-6 right-6 top-4 h-0.5 bg-slate-200 -z-0" />

          {workflowStages.map((stage, idx) => {
            const isCompleted = idx < currentStageIndex;
            const isCurrent = idx === currentStageIndex;

            let circleClass = 'bg-slate-100 text-slate-400 border-2 border-slate-300';
            let icon = <span className="text-xs font-bold">{idx + 1}</span>;

            if (isCompleted) {
              circleClass = 'bg-emerald-600 text-white border-2 border-emerald-600';
              icon = <Check className="w-3.5 h-3.5 stroke-[3]" />;
            } else if (isCurrent) {
              if (isRejected) {
                circleClass = 'bg-rose-600 text-white border-2 border-rose-600 ring-4 ring-rose-100';
                icon = <XCircle className="w-3.5 h-3.5" />;
              } else if (isRevision || isConflict) {
                circleClass = 'bg-amber-500 text-white border-2 border-amber-500 ring-4 ring-amber-100';
                icon = <AlertTriangle className="w-3.5 h-3.5" />;
              } else {
                circleClass = 'bg-blue-600 text-white border-2 border-blue-600 ring-4 ring-blue-100';
                icon = <Clock className="w-3.5 h-3.5 animate-pulse" />;
              }
            }

            return (
              <div key={stage.id} className="flex flex-col items-center relative z-10 text-center w-20">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${circleClass}`}>
                  {icon}
                </div>
                <span
                  className={`text-[11px] mt-2 font-medium leading-tight max-w-[80px] ${
                    isCurrent
                      ? isRejected
                        ? 'text-rose-600 font-bold'
                        : isRevision || isConflict
                        ? 'text-amber-600 font-bold'
                        : 'text-blue-700 font-bold'
                      : isCompleted
                      ? 'text-slate-700'
                      : 'text-slate-400'
                  }`}
                >
                  {stage.name}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
