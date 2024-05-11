'use client';
import { useState, useEffect } from "react";
import axios from "axios";

export default function Home() {

  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loadingForFile, setLoadingForFile] = useState(false);
  const [chats,setChats] = useState([{
    user: "llm",
    text:"Hello, how can I help you?"
  }]);

  const [userChat, setUserChat] = useState("");

  const handleTextChange = (e) => {
    setUserChat(e.target.value);
 }

 const getResponse = async () => {
    if(userChat == "") return;
    chats.push({
      user: "user", 
      text: userChat
    });
    setLoading(true);
    console.log(userChat);
    const response = await axios.get(`http://127.0.0.1:5000/ask?query=${userChat}`);
    setUserChat("")
    console.log(response);
    chats.push({
      user: "llm", 
      text: response.data.result
    });
    setLoading(false);
 }

  const handleFileChange = async(e) => {
    setSelectedFile(e.target.files[0]);
  };

  const uploadFile = async () => {
    setLoadingForFile(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await axios.post("http://127.0.0.1:5000/load", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    
    });
    console.log(response.data);

    if(response.data.status == "success") {
      alert("File uploaded successfully");
    }else{
      alert("File upload failed");
    }
    setLoadingForFile(false);
    setSelectedFile(null);
  }


 return (
  <div data-theme="dark" className="h-screen flex flex-col">
    <div className="overflow-y-auto border border-slate-300 hover:border-slate-400 mx-20 my-10 rounded-lg flex-1">
      {chats.length !== 0 ? (
        <div>
          {chats.map((chat, ind) => (
            <div key={ind} className={chat.user === "user" ? "chat chat-end" : "chat chat-start"}>
              <div className="chat-bubble m-5">{chat.text}</div>
            </div>
          ))}
        </div>
      ) : <p>No chats available</p>}

      <div className={loading ? "chat chat-start" : "hidden"}>
        <div className="skeleton chat-bubble m-5">loading...</div>
        {/* <span className="loading loading-dots loading-l"></span> */}
      </div>
    </div>

    <div data-theme="dark" className="flex justify-center m-10">
      <input
        type="file"
        accept=".pdf"
        className={"file-input file-input-bordered w-full max-w-xs"}
        onChange={handleFileChange}
      />
      <button className="btn btn-primary" type="submit" onClick={uploadFile}>upload</button>
      <span className={loadingForFile ? "loading loading-spinner loading-lg" : "hidden"}></span>
      <input type="text" placeholder="Type here" className="input input-bordered w-full mx-10" value={userChat} onChange={handleTextChange} />
      <button className="btn btn-primary" type="submit" onClick={getResponse}>Ask</button>
    </div>
  </div>
);}
