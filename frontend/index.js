const form1 = document.querySelector("#create_game_input");
const form2 = document.querySelector("#join_game_input");

let websocket = new WebSocket("ws://localhost:8765/");

window.addEventListener("DOMContentLoaded", () => {
	
});

form1.addEventListener("submit", handler);
form2.addEventListener("submit", handler);


function handler(evt) {
	// verhindere Standardverhalten des Formulars
	evt.preventDefault();

	// holt die input Elemente
	const inputs = evt.target.querySelectorAll("input");

	// extrahiert die Daten
	const data = Array.from(inputs).map((input) => [input.id, input.value]);
	

	// logt die Daten in der Console des Browsers.
	console.log(data);
	websocket.send(JSON.stringify(data));

}

websocket.addEventListener("message", ({ data }) => {
	const event = JSON.parse(data);
	console.log(event)
	switch (event.type) {
		case "new_game":
			// store game id
			console.log(event);
			document.getElementById("current_gameid").innerHTML= event.game_id
	}


});