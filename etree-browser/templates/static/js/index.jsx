//Simple react app to load a component from router file (routes.js) into index.html
import React from 'react';
import ReactDOM from 'react-dom';
import routes from  "./routes";

ReactDOM.render(routes,document.getElementById("content"));
