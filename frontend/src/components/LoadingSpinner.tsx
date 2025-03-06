import React from "react";

interface LoadingSpinnerProps {
    size?: string;
    color?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
                                                           size = "w-8 h-8",
                                                           color = "border-primary",
                                                       }) => {
    return (
        <div
            className={`border-4 border-t-transparent rounded-full animate-spin ${size} ${color}`}
        ></div>
    );
};

export default LoadingSpinner;
