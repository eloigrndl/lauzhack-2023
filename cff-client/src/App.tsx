import React, { useState } from "react";
import NavBar from "./components/NavBar/NavBar";
import Form from "./components/Form/Form";
import { Trip } from "./types/api_types";
import TripList from "./components/TripList/TripList";

function App() {
  const [trips, setTrips] = useState([] as Trip[]);

  return (
    <div className="h-full flex flex-col">
      <NavBar />
      <div className="flex flex-col gap-3">
        <Form setTripList={setTrips} />

        <TripList tripList={trips} />
      </div>
    </div>
  );
}

export default App;
