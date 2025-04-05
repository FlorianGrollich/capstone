import * as React from "react";

const CreateProjectButton: React.FC = () => {
    return (
        <div className="group flex flex-col items-center justify-center border-gray-400 hover:border-primary hover:bg-gray-50 cursor-pointer border-dotted border-2 h-48 aspect-video rounded-lg transition-all duration-200">
            <div className="text-4xl text-gray-400 group-hover:text-primary transition-colors">
                +
            </div>
            <span className="text-sm text-gray-500 group-hover:text-primary mt-2 transition-colors">Create Project</span>
        </div>
    );
};

export default CreateProjectButton;