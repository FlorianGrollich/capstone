import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {RootState} from "../../../store.ts";

interface RegisterFormState {
    email: string;
    password: string;
    repeatPassword: string;
}

const initialState: RegisterFormState = {
    email: '',
    password: '',
    repeatPassword: '',
};

const registerFormSlice = createSlice({
    name: 'registerForm',
    initialState,
    reducers: {
        setEmail: (state, action: PayloadAction<string>) => {
            state.email = action.payload;
        },
        setPassword: (state, action: PayloadAction<string>) => {
            state.password = action.payload;
        },
        setRepeatPassword: (state, action: PayloadAction<string>) => {
            state.repeatPassword = action.payload;
        },
    },
});

export const selectEmail = (state: RootState) => state.registerForm.email;
export const selectPassword = (state: RootState) => state.registerForm.password;

export const {setEmail, setPassword, setRepeatPassword} = registerFormSlice.actions;
export default registerFormSlice.reducer;