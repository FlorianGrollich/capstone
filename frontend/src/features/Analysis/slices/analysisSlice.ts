import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { ProjectResponse, StatsData, StatValues } from "../types";
import axiosClient from "../../../api/axiosClient.ts";
import axios from "axios";

// Type for frontend use that extends ProjectResponse with video_url instead of file_url
interface ProjectData extends Omit<ProjectResponse, 'file_url'> {
    video_url: string;
}

interface AnalysisState {
    projectData: ProjectData | null;
    loading: 'idle' | 'pending' | 'succeeded' | 'failed';
    error: string | null;
    currentTime: number;
    currentStats: StatValues;
}

const calculateCurrentStats = (
    statsData: StatsData | undefined | null,
    currentTimeSeconds: number
): StatValues => {
    // Default stats with null values
    const defaultStats: StatValues = {
        POSSESSION: null,
        PASS: null,
    };

    if (!statsData) {
        return defaultStats;
    }

    const currentTimeMs = currentTimeSeconds * 1000;
    const sortedTimestamps = Object.keys(statsData)
        .map(Number)
        .sort((a, b) => a - b);

    const relevantTimestamps = sortedTimestamps.filter(ts => ts <= currentTimeMs);

    // Start with default stats and merge in the values from each timestamp
    return relevantTimestamps.reduce<StatValues>(
        (acc, ts) => {
            const statsAtTs = statsData[String(ts)];

            // For each stat type (POSSESSION, PASS)
            Object.keys(statsAtTs).forEach((statType) => {
                const key = statType as keyof StatValues;
                const statValue = statsAtTs[key];

                if (statValue) {
                    acc[key] = statValue;
                }
            });

            return acc;
        },
        JSON.parse(JSON.stringify(defaultStats))
    );
};

const initialState: AnalysisState = {
    projectData: null,
    loading: 'idle',
    error: null,
    currentTime: 0,
    currentStats: {
        POSSESSION: null,
        PASS: null,
    },
};

export const fetchProjectData = createAsyncThunk<ProjectData, string, { rejectValue: string }>(
    'analysis/fetchProjectData',
    async (projectId, { rejectWithValue }) => {
        try {
            const response = await axiosClient.get<ProjectResponse>(`/project/${projectId}`);
            if (!response.data || !response.data.file_url || !response.data.analysis_results.stats) {
                throw new Error("Invalid project data received");
            }

            // Transform ProjectResponse to ProjectData (file_url → video_url)
            const projectData: ProjectData = {
                _id: response.data._id,
                email: response.data.email,
                video_url: response.data.file_url,
                status: response.data.status,
                title: response.data.title,
                analysis_results: response.data.analysis_results
            };

            return projectData;
        } catch (error) {
            let errorMessage = "Failed to fetch project data";
            if (axios.isAxiosError(error) && error.response) {
                errorMessage = `Error ${error.response.status}: ${error.response.data?.message || error.message}`;
            } else if (error instanceof Error) {
                errorMessage = error.message;
            }
            return rejectWithValue(errorMessage);
        }
    }
);

const analysisSlice = createSlice({
    name: 'analysis',
    initialState,
    reducers: {
        updateCurrentTime: (state, action: PayloadAction<number>) => {
            state.currentTime = action.payload;
            state.currentStats = calculateCurrentStats(
                state.projectData?.analysis_results.stats,
                state.currentTime
            );
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchProjectData.pending, (state) => {
                state.loading = 'pending';
                state.error = null;
            })
            .addCase(fetchProjectData.fulfilled, (state, action: PayloadAction<ProjectData>) => {
                state.loading = 'succeeded';
                state.projectData = action.payload;
                state.currentStats = calculateCurrentStats(
                    state.projectData.analysis_results.stats,
                    state.currentTime
                );
                state.error = null;
            })
            .addCase(fetchProjectData.rejected, (state, action) => {
                state.loading = 'failed';
                state.error = action.payload ?? "Unknown error occurred";
                state.projectData = null;
            });
    },
});

export const { updateCurrentTime } = analysisSlice.actions;
export default analysisSlice.reducer;