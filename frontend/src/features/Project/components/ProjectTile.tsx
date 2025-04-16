import React from 'react';
import {Project} from '../slices/projectSlice';
import {FiLoader, FiAlertCircle, FiVideo} from 'react-icons/fi';
import {useNavigate} from 'react-router-dom';

interface ProjectTileProps {
    project: Project;
}

const ProjectTile: React.FC<ProjectTileProps> = ({project}) => {

    const renderContent = () => {
        switch (project.status) {
            case 'loading':
                return (
                    <div className="flex flex-col items-center justify-center h-full">
                        <FiLoader className="h-16 w-16 text-primary mb-3"/>
                        <p className="font-semibold text-gray-600">Processing...</p>
                    </div>
                );
            case 'error':
                return (
                    <div className="flex flex-col items-center justify-center h-full">
                        <FiAlertCircle className="h-16 w-16 text-red-500 mb-3"/>
                        <p className="font-semibold text-red-600">Error</p>
                    </div>
                );
            case 'finished':
                return (
                    <div className="flex flex-col items-center justify-center">
                        <FiVideo className="h-16 w-16 text-primary mb-3"/>
                        <p className="font-semibold text-gray-600">Ready to view</p>
                    </div>
                );
        }
    };

    const navigate = useNavigate();

    return (
        <div
            className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow w-full h-48 cursor-pointer"
            onClick={() => navigate(`/analysis/${project._id}`)}>
            <div className="bg-gray-100 relative flex items-center justify-center">
                {renderContent()}
            </div>
            <div className="p-3 h-6">
                <h3 className="font-medium text-gray-800">{project.title}</h3>
                <p className="text-sm text-gray-500 capitalize mt-1">{project.status}</p>
            </div>
        </div>
    );
};

export default ProjectTile;