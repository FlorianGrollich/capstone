import {ButtonHTMLAttributes} from "react";
import * as React from "react";

const Button: React.FC<ButtonHTMLAttributes<HTMLButtonElement>> = ({ className, children, ...props}) => {

    return (
        <button
            className={`${className} px-4 py-2 rounded-lg font-medium transition duration-300 flex items-center justify-center bg-primary text-white hover:bg-primary-dark`} {...props}>
            {children}
        </button>
    );
};

export default Button;
