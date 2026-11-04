import React from 'react';

interface LogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showSubtitle?: boolean;
  subtitleText?: string;
  color?: string;
}

export const Logo: React.FC<LogoProps> = ({
  className = '',
  size = 'md',
  showSubtitle = true,
  subtitleText = 'NAIL CARE • BEAUTY • MORE THAN A LOOK',
  color = 'text-darkRose'
}) => {
  const iconSizes = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl md:text-4xl'
  };

  const subSizes = {
    sm: 'text-[9px] tracking-widest',
    md: 'text-[10px] tracking-widest',
    lg: 'text-xs tracking-[0.25em]'
  };

  return (
    <div className={`flex flex-col items-center select-none ${className}`}>
      {/* Delicate floral line-art logo icon */}
      <svg
        className={`${iconSizes[size]} text-rosePink mb-1 transition-transform duration-300 hover:scale-105`}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Center petal */}
        <path
          d="M50 20 C42 40 46 65 50 80 C54 65 58 40 50 20 Z"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Left petal */}
        <path
          d="M48 45 C30 35 18 50 26 70 C35 75 44 72 48 65"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Right petal */}
        <path
          d="M52 45 C70 35 82 50 74 70 C65 75 56 72 52 65"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Sparkle top right */}
        <path
          d="M68 25 L70 30 L75 32 L70 34 L68 39 L66 34 L61 32 L66 30 Z"
          fill="currentColor"
          opacity="0.8"
        />
      </svg>

      <span className={`font-playfair font-medium ${textSizes[size]} ${color} tracking-tight`}>
        Emmay Beauty
      </span>

      {showSubtitle && (
        <span className={`font-montserrat font-medium text-dustyRose/80 uppercase mt-0.5 ${subSizes[size]}`}>
          {subtitleText}
        </span>
      )}
    </div>
  );
};
