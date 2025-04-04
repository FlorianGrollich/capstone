import {useSelector} from "react-redux";
import {selectToken} from "../slices/authState.ts";
import React, {useEffect} from "react";
import {useNavigate} from "react-router-dom";

const Redirect: React.FC = () => {

    const token = useSelector(selectToken);
    const navigate = useNavigate();

    useEffect(() => {
        if(token !== null) {
            navigate("/");
        }
    }, [navigate, token]);

    return (<div></div>);
};

export default Redirect;