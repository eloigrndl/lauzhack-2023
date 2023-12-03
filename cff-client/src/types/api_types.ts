export interface Place {
  id: number;
  name: string;
  geoloc: [number, number];
}

export interface Trip {
  originName: string;
  destinationName: string;
  departure_time: string;
  arrival_time: string;
  duration: number;
  legs: [
    {
      originName: string;
      destinationName: string;
      departure_time: string;
      arrival_time: string;
      duration: number;
    }
  ];
  co2Emission: number;
}
