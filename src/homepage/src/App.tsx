import React from 'react';
import { useEffect } from "react";
import logo from './logo.svg';
import { ListGroup, Button } from "react-bootstrap";
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css'

function App() {
  useEffect(() => {
    document.title = "Tesla-ver"
  }, []);
  return (
    <div className="App">
      <header className="App-header">
        <p>Tesla-ver</p>
        <p>Tesla-ver is a microbiome graphing tool</p>
        <ListGroup horizontal>
          <ListGroup.Item><Button variant="primary" onClick={(e) => {
            e.preventDefault();
            window.location.href = '/datauploading.html';
          }}>Data Uploading</Button></ListGroup.Item>
          <ListGroup.Item><Button variant="success" onClick={(e) => {
            e.preventDefault();
            window.location.href = '/bubblechart.html';
          }}>Bubble Chart</Button></ListGroup.Item>
        </ListGroup>
      </header>
    </div>
  );
}

export default App;
