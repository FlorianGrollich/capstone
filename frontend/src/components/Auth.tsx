import React, {useEffect} from "react";
import {useNavigate} from "react-router-dom";


const Auth: React.FC = () => {
    const token = localStorage.getItem('token');
    const navigate = useNavigate();

    useEffect(() => {
        console.log("token: ", token);
        if (token === undefined || token === null) {
            navigate("/login");
        }
    }, [navigate, token]);

    return (
        <div>
        </div>
    );
};

export default Auth;