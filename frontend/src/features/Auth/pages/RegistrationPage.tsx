import * as React from "react";
import TextField from "../../../components/TextField.tsx";
import Button from "../../../components/Button.tsx";
import {useNavigate} from "react-router-dom";
import {useDispatch, useSelector} from "react-redux";
import {AppDispatch, RootState} from "../../../store.ts";
import {setEmail, setPassword, setRepeatPassword} from "../slices/registerFormState.ts";
import {register} from "../slices/authState.ts";
import {selectEmail, selectPassword} from "../slices/registerFormState.ts";
import Redirect from "../components/redirect.tsx";
import {validateEmail} from "../utils/validation.ts";
import {useEffect} from "react";

const RegistrationPage: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch<AppDispatch>();
    const email = useSelector(selectEmail);
    const password = useSelector(selectPassword);
    const repeatPassword = useSelector((state: RootState) => state.registerForm.repeatPassword);
    const loading = useSelector((state: RootState) => state.authState.loading);
    const token = useSelector((state: RootState) => state.authState.token);
    const authError = useSelector((state: RootState) => state.authState.error);

    const [emailError, setEmailError] = React.useState<string | undefined>(undefined);
    const [passwordError, setPasswordError] = React.useState<string | undefined>(undefined);


    useEffect(() => {
        if (token) {
            navigate('/');
        }
    }, [token, navigate]);

    const handleRegister = () => {

        if (!validateEmail(email)) {
            setEmailError("Please enter a valid email address");
            return;
        }
        setEmailError(undefined);

        if (password !== repeatPassword) {
            setPasswordError("Passwords don't match");
            return;
        }
        setPasswordError(undefined);

        dispatch(register({email, password}));
    };

    return (
        <div className={"h-screen bg-gradient-to-tr from-primary to-accent flex items-center justify-center"}>
            <Redirect/>
            <div className="bg-white rounded-xl p-4 w-1/3">
                {authError && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        <p className="text-sm">{authError}</p>
                    </div>
                )}

                <TextField
                    onChange={(value) => {
                        dispatch(setEmail(value.target.value));
                        setEmailError(undefined);
                    }}
                    label={"Email"}
                    error={emailError}
                    disabled={loading}
                />
                <div className="h-4"></div>
                <TextField
                    type="password"
                    onChange={(value) => {
                        dispatch(setPassword(value.target.value));
                        setPasswordError(undefined);
                    }}
                    label={"Password"}
                    disabled={loading}
                />
                <div className="h-4"></div>
                <TextField
                    type="password"
                    onChange={(value) => {
                        dispatch(setRepeatPassword(value.target.value));
                        setPasswordError(undefined);
                    }}
                    label={"Repeat Password"}
                    error={passwordError}
                    disabled={loading}
                />

                <div className="h-4"></div>
                <Button
                    className={"w-full"}
                    onClick={handleRegister}
                    disabled={loading}
                >
                    {loading ? "Registering..." : "Register"}
                </Button>
                <div className={"h-2"}></div>
                <p className={"text-xs text-gray-600"}>
                    Already have an account?{" "}
                    <button
                        className={"hover:underline text-primary"}
                        onClick={() => navigate("/login")}
                        disabled={loading}
                    >
                        Sign In
                    </button>
                </p>
            </div>
        </div>
    );
};

export default RegistrationPage;