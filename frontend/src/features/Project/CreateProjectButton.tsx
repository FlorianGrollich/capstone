import * as React from "react";
import {useNavigate} from "react-router-dom";

const CreateProjectButton: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div onClick={() => navigate("/upload")}
             className="group flex flex-col items-center justify-center border-gray-400 hover:border-primary hover:bg-gray-50 cursor-pointer border-dotted border-2 h-48 aspect-video rounded-lg transition-all duration-200">
            <div className="text-4xl text-gray-400 group-hover:text-primary">
                +
            </div>
            <span className="text-sm text-gray-400 group-hover:text-primary mt-2">Create Project</span>
        </div>
    );
};

export default CreateProjectButton;