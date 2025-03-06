import React from "react";

interface TextFieldProps {
    label: string;
    type?: "text" | "email" | "password" | "number";

    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    placeholder?: string;
    error?: string;
    required?: boolean;
    disabled?: boolean;
    className?: string;
}

const TextField: React.FC<TextFieldProps> = ({
                                                 label,
                                                 type = "text",
                                                 onChange,
                                                 placeholder,
                                                 error,
                                                 required = false,
                                                 disabled = false,
                                                 className = "",
                                             }) => {
    return (
        <div className={`flex flex-col ${className}`}>
            <label className="text-sm font-medium text-gray-700 mb-2">
                {label} {required && <span className="text-red-500">*</span>}
            </label>
            <input
                type={type}
                onChange={onChange}
                placeholder={placeholder}
                disabled={disabled}
                className={`px-4 py-2 border rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary ${
                    error ? "border-red-500" : "border-gray-300"
                } ${disabled ? "bg-gray-200 cursor-not-allowed" : ""}`}
            />
            {error && <span className="text-red-500 text-sm mt-1">{error}</span>}
        </div>
    );
};

export default TextField;


