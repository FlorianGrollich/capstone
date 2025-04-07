import React, {useEffect} from "react";
import {useDispatch, useSelector} from 'react-redux';
import {fetchProjects, Project, selectProject} from '../slices/projectSlice';
import ProjectTile from '../components/ProjectTile';
import CreateProjectButton from "../CreateProjectButton.tsx";
import {FiLoader} from 'react-icons/fi';
import {AppDispatch} from "../../../store.ts";

const ProjectMenu: React.FC = () => {
    const dispatch = useDispatch<AppDispatch>();
    const {projects, status, error} = useSelector(selectProject);

    useEffect(() => {
        dispatch(fetchProjects());
    }, [dispatch]);

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800">My Projects</h1>
                <CreateProjectButton/>
            </div>

            {status === 'loading' && (
                <div className="text-center py-10">
                    <FiLoader className="animate-spin h-10 w-10 mx-auto mb-3 text-primary"/>
                    <p className="text-gray-600">Loading projects...</p>
                </div>
            )}

            {status === 'failed' && (
                <div className="text-center py-10 text-red-600">
                    <p className="font-semibold">{error || 'Failed to load projects'}</p>
                    <button
                        onClick={() => dispatch(fetchProjects())}
                        className="mt-4 px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark transition"
                    >
                        Try Again
                    </button>
                </div>
            )}

            {status === 'succeeded' && (
                <>
                    {projects.length === 0 ? (
                        <div className="text-center py-10">
                            <p className="text-gray-600">No projects yet. Create your first project!</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {projects.map((project: Project, index: React.Key | null | undefined) => (
                                <ProjectTile key={index} project={project}/>
                            ))}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default ProjectMenu;