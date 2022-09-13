import React, { Component } from "react";
import { render } from "react-dom";

export default class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    console.log(1);
    return (
      <dev>
        <link
          href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css"
          rel="stylesheet"
        />
        <button class="bg-indigo-700 font-semibold text-white py-2 px-4 rounded">
          ボタン
        </button>
        <h1>Hello I'm Mdakkori.</h1>
      </dev>
    );
  }
}

const appDiv = document.getElementById("app");
render(<App />, appDiv);
