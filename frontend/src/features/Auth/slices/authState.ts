import {createSlice, PayloadAction, createAsyncThunk} from '@reduxjs/toolkit';
import  {AxiosError} from 'axios';
import axiosClient from "../../../api/axiosClient.ts";

interface AuthState {
    token: string | null;
    loading: boolean;
    error: string | null;
}

const initialState: AuthState = {
    token: localStorage.getItem('token'),
    loading: false,
    error: null,
};

export const login = createAsyncThunk(
    'auth/login',
    async ({email, password}: { email: string; password: string }, {rejectWithValue}) => {
        try {
            const response = await axiosClient.post('/login', {email, password});
            return response.data;
        } catch (error) {
            const e = error as AxiosError;
            return rejectWithValue(e);
        }
    }
);

export const register = createAsyncThunk(
    'auth/register',
    async ({email, password}: { email: string; password: string }, {rejectWithValue}) => {
        try {
            const response = await axiosClient.post('/register', {email, password});
            return response.data;

        } catch (error) {
            console.log("Error creating register: ", error);
            return rejectWithValue(error ?? 'An unknown error occurred');
        }
    }
);

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logout: (state) => {
            state.token = null;
            localStorage.removeItem('token');
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(login.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(login.fulfilled, (state, action: PayloadAction<string>) => {
                state.loading = false;
                state.token = action.payload;
                localStorage.setItem('token', action.payload);
            })
            .addCase(login.rejected, (state) => {
                state.loading = false;
            })
            .addCase(register.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(register.fulfilled, (state, action: PayloadAction<string>) => {
                state.loading = false;
                state.token = action.payload;
                console.log("set token", action.payload);
                localStorage.setItem('token', action.payload);
            })
            .addCase(register.rejected, (state) => {
                state.loading = false;

            });
    },
});

export const selectToken = (state: AuthState) => state.token;

export const {logout} = authSlice.actions;
export default authSlice.reducer;