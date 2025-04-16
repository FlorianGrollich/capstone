import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import {ProjectData, StatsData, CurrentStats,  StatValues} from "../types";
import axiosClient from "../../../api/axiosClient.ts";
import axios from "axios";


interface AnalysisState {
    projectData: ProjectData | null;
    loading: 'idle' | 'pending' | 'succeeded' | 'failed';
    error: string | null;
    currentTime: number;
    currentStats: CurrentStats;
}


const calculateCurrentStats = (
    statsData: StatsData | undefined | null,
    currentTimeSeconds: number
): CurrentStats => {
    const defaultStats: CurrentStats = {
        POSSESSION: {},
        PASS: {},
    };
    if (!statsData) {
        return defaultStats;
    }

    const currentTimeMs = currentTimeSeconds * 1000;
    const sortedTimestamps = Object.keys(statsData)
        .map(Number)
        .sort((a, b) => a - b);

    const relevantTimestamps = sortedTimestamps.filter(ts => ts <= currentTimeMs);

    const mergedStats = relevantTimestamps.reduce<CurrentStats>(
        (acc, ts) => {
            const statsAtTs = statsData[String(ts)];
            for (const statType in statsAtTs) {
                if (!acc[statType as keyof CurrentStats]) {
                    acc[statType as keyof CurrentStats] = {};
                }

                const teamStats = statsAtTs[statType as keyof StatValues];
                if (teamStats) {
                    const currentStatType = acc[statType as keyof CurrentStats];
                    if(currentStatType) { // Type guard
                        if (teamStats.team1 !== undefined) {
                            currentStatType.team1 = teamStats.team1;
                        }
                        if (teamStats.team2 !== undefined) {
                            currentStatType.team2 = teamStats.team2;
                        }
                    }
                }
            }
            return acc;
        },
        JSON.parse(JSON.stringify(defaultStats))
    );

    return mergedStats;
};



const initialState: AnalysisState = {
    projectData: null,
    loading: 'idle',
    error: null,
    currentTime: 0,
    currentStats: {
        POSSESSION: {},
        PASS: {},
    },
};


export const fetchProjectData = createAsyncThunk<ProjectData, string, { rejectValue: string }>(
    'analysis/fetchProjectData',
    async (projectId, { rejectWithValue }) => {
        try {
            const response = await axiosClient.get<ProjectData>(`/project/${projectId}`);
            if (!response.data || !response.data.video_url || !response.data.stats) {
                throw new Error("Invalid project data received");
            }
            return response.data;
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
            state.currentStats = calculateCurrentStats(state.projectData?.stats, state.currentTime);
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
                state.currentStats = calculateCurrentStats(state.projectData.stats, state.currentTime);
                state.error = null;
            })
            .addCase(fetchProjectData.rejected, (state, action) => {
                state.loading = 'failed';
                state.error = action.payload ?? "Unknown error occurred"; // Use rejectValue
                state.projectData = null;
            });
    },
});

export const { updateCurrentTime } = analysisSlice.actions;
export default analysisSlice.reducer;