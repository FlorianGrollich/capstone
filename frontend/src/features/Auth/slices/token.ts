import {createSlice, PayloadAction, createAsyncThunk} from '@reduxjs/toolkit';
import axios from 'axios';

interface TokenState {
    token: string | null;
    loading: boolean;
    error: string | null;
}

const initialState: TokenState = {
    token: null,
    loading: false,
    error: null,
};

// Async thunk for login
export const login = createAsyncThunk(
    'token/login',
    async ({email, password}: { email: string; password: string }, {rejectWithValue}) => {
        try {
            const response = await axios.post('/api/login', {email, password});
            return response.data.token;
        } catch (error) {
            return rejectWithValue(error);
        }
    }
);

const tokenSlice = createSlice({
    name: 'token',
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(login.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(login.fulfilled, (state, action: PayloadAction<string>) => {
                state.loading = false;
                state.token = action.payload;
            })
            .addCase(login.rejected, (state, action: PayloadAction<unknown>) => {
                state.loading = false;
                if (typeof action.payload === 'string') {
                    state.error = action.payload;
                } else {
                    state.error = 'An unknown error occurred';
                }
            });
    },
});

export default tokenSlice.reducer;