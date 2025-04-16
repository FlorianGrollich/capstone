import React from 'react';
import {Project} from '../slices/projectSlice';
import {FiLoader, FiAlertCircle, FiVideo} from 'react-icons/fi';
import {useNavigate} from 'react-router-dom';

interface ProjectTileProps {
    project: Project;
}

const ProjectTile: React.FC<ProjectTileProps> = ({project}) => {
    const navigate = useNavigate();
    const isLoading = project.status === 'loading';

    const renderContent = () => {
        switch (project.status) {
            case 'loading':
                return (
                    <div className="flex flex-col items-center justify-center h-full">
                        <FiLoader className="h-16 w-16 text-primary mb-3 animate-spin"/>
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

    const handleClick = () => {
        if (!isLoading) {
            navigate(`/analysis/${project._id}`);
        }
    };

    return (
        <div
            className={`border rounded-lg overflow-hidden shadow-sm transition-shadow w-full h-48
                      ${isLoading ? 'bg-gray-200 opacity-70' : 'hover:shadow-md cursor-pointer'}`}
            onClick={handleClick}>
            <div className={`${isLoading ? 'bg-gray-200' : 'bg-gray-100'} relative flex items-center justify-center`}>
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