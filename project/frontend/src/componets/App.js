import React, { Component } from "react";
import { render } from "react-dom";

export default class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    console.log(1);
    return <h1>Hello I'm Makkori.</h1>;
  }
}

const appDiv = document.getElementById("app");
render(<App />, appDiv);