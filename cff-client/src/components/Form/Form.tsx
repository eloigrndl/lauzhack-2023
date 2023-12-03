import { useState } from "react";
import { Place, Trip } from "../../types/api_types";
import SearchBar from "./SearchBar";

import axios from "axios";

interface FormProps {
  setTripList: React.Dispatch<React.SetStateAction<Trip[]>>;
}

export default function Form({ setTripList }: FormProps) {
  const [originPlace, setOriginPlace] = useState({} as Place);
  const [destinationPlace, setDestinationPlace] = useState({} as Place);
  const [date, setDate] = useState(new Date());

  async function fetchTrips() {
    try {
      if (originPlace.name && originPlace.name) {
        const response = await axios.post(
          `${process.env.REACT_APP_TRIPS_API_URL}?date=${date
            .toISOString()
            .split("T")[0]
            .toString()}&time=${date.toLocaleTimeString().slice(0, 5)}`,
          {
            origin: originPlace,
            destination: destinationPlace,
          }
        );
        setTripList(response.data);
        console.log(response.data);
      }
    } catch (error) {
      console.error("Error fetching suggestions:", error);
    }
  }

  return (
    <div className="flex flex-row justify-center">
      <div className="flex flex-col w-3/4 bg-cff-charcoal text-white border-[1px] rounded-md gap-2 justify-center items-center py-3">
        <SearchBar placeholder="From" setValue={setOriginPlace} />
        <SearchBar placeholder="To" setValue={setDestinationPlace} />
        <input
          className="rounded-md text-gray-100 p-2 bg-cff-charcoal border-[1px] border-cff-anthracite"
          type="datetime-local"
          name="date"
          id="date"
          defaultValue={date.toString()}
          onChange={(e) => setDate(new Date(e.target.value))}
        />
        <button className="bg-cff-red rounded-md p-2" onClick={fetchTrips}>
          Search
        </button>
      </div>
    </div>
  );
}
