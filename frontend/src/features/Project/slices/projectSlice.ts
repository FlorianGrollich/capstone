import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import {RootState} from "../../../store.ts";
import axiosClient from "../../../api/axiosClient.ts";

export interface Project {
    _id: string;
    title: string;
    status: 'finished' | 'loading' | 'error';
}

export interface ProjectsState {
    projects: Project[];
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    error: string | null;
}

const initialState: ProjectsState = {
    projects: [],
    status: 'idle',
    error: null
};

export const fetchProjects = createAsyncThunk(
    'projects/fetchProjects',
    async (_, {rejectWithValue}) => {
        try {
            const response = await axiosClient.get('/projects');
            return response.data;
        } catch (e) {
            return rejectWithValue(`Failed to fetch projects ${e}`,);
        }
    }
);

const projectsSlice = createSlice({
    name: 'projects',
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchProjects.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(fetchProjects.fulfilled, (state, action) => {
                state.status = 'succeeded';
                state.projects = action.payload;
            })
            .addCase(fetchProjects.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.payload as string || 'Failed to fetch projects';
            });
    }
});

export const selectProject = (state: RootState) => state.project;


export default projectsSlice.reducer;