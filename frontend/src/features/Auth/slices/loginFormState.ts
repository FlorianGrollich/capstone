import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {RootState} from "../../../store.ts";

interface LoginFormState {
    email: string;
    password: string;
}

const initialState: LoginFormState = {
    email: '',
    password: '',
};

const loginFormSlice = createSlice({
    name: 'loginForm',
    initialState,
    reducers: {
        setEmail: (state, action: PayloadAction<string>) => {
            state.email = action.payload;
        },
        setPassword: (state, action: PayloadAction<string>) => {
            state.password = action.payload;
        },
    },
});

export const selectEmail = (state: RootState) => state.loginForm.email;
export const selectPassword = (state: RootState) => state.loginForm.password;

export const {setEmail, setPassword} = loginFormSlice.actions;
export default loginFormSlice.reducer;