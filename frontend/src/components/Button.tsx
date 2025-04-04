import React, { ButtonHTMLAttributes } from "react";

const Button: React.FC<ButtonHTMLAttributes<HTMLButtonElement>> = ({ className, children, ...props}) => {
    return (
        <button
            className={`
                px-4 py-2 rounded-lg font-medium transition duration-300
                flex items-center justify-center
                bg-primary text-white hover:bg-primary-dark
                disabled:opacity-60 disabled:cursor-not-allowed  // Added disabled styles
                ${className} // Allow className prop to override or add styles
            `}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;