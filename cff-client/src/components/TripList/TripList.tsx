import { useState } from "react";
import { Place, Trip } from "../../types/api_types";
import TripCard from "./TripCard";

interface TripListProps {
  tripList: Trip[];
}

const labels = ["Public transport only", "Car only", "P+Rail intermodal"];

export default function TripList({ tripList }: TripListProps) {
  if (tripList.length === 0) {
    return (
      <div className="flex flex-row justify-center">
        <div className="w-11/12 bg-cff-charcoal text-gray-300 border-cff-anthracite rounded-md flex flex-col items-center gap-1 p-3">
          <h1 className="text-lg">No trips found...</h1>
          <p className="text-md">Try changing your search parameters</p>
        </div>
      </div>
    );
  }
  return (
    <div className="flex flex-col items-center p-1">
      <div className="w-10/12 bg-cff-charcoal text-white border-cff-anthracite rounded-md flex flex-col gap-5">
        {tripList.map((trip, index) => (
          <TripCard key={index} trip={trip} label={labels[index]} />
        ))}
      </div>
    </div>
  );
}
