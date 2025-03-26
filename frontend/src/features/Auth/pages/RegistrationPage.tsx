import * as React from "react";
import TextField from "../../../components/TextField.tsx";
import Button from "../../../components/Button.tsx";
import {FcGoogle} from "react-icons/fc";
import {useNavigate} from "react-router-dom";
import {useDispatch} from "react-redux";
import {AppDispatch} from "../../../store.ts";
import {setEmail, setPassword, setRepeatPassword} from "../slices/registerFormState.ts";

const RegistrationPage: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch<AppDispatch>();

    return (
        <div className={"h-screen bg-gradient-to-tr from-primary to-accent flex items-center justify-center"}>
            <div className="bg-white rounded-xl p-4 w-1/3">
                <TextField onChange={(value) => {
                    dispatch(setEmail(value.target.value));
                }} label={"Email"}/>
                <div className="h-4"></div>
                <TextField onChange={(value) => {
                    dispatch(setPassword(value.target.value));
                }} label={"Password"}/>
                <div className="h-4"></div>
                <TextField onChange={(value) => {
                    dispatch(setRepeatPassword(value.target.value));
                }} label={"Repeat Password"}/>

                <div className="h-4"></div>
                <Button className={"w-full"}>Register</Button>
                <div className={"h-2"}></div>
                <p className={"text-xs text-gray-600"}>
                    Already have an account?{" "}
                    <button className={"hover:underline text-primary"} onClick={() => navigate("/login")}>Sign In
                    </button>
                </p>

                <div className="relative my-4 w-full">
                    <hr className="border-t-2 border-gray-300"/>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="bg-white px-2 text-gray-500">or</span>
                    </div>
                </div>

                <button
                    className={"px-4 py-2.5 rounded-lg font-medium transition duration-300 flex items-center justify-center bg-white border-2 border-gray-300 text-black w-full hover:border-primary  hover:shadow-lg"}>
                    <FcGoogle/></button>
            </div>
        </div>
    );
};

export default RegistrationPage;