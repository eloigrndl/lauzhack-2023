import { Trip } from "../../types/api_types";
import {
  Timeline,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineItem,
  TimelineOppositeContent,
  TimelineSeparator,
} from "@mui/lab";
import Home from "@mui/icons-material/Home";
import FmdGood from "@mui/icons-material/FmdGood";
import Commute from "@mui/icons-material/Commute";

import { Typography } from "@mui/material";

interface TripCardProps {
  trip: Trip;
  label: string;
}

export default function TripCard({ trip, label }: TripCardProps) {
  console.log(trip);
  return (
    <div className="flex flex-col items-center">
      <div className="w-3/4 border-[1px] border-cff-anthracite rounded-t-md flex flex-row justify-evenly">
        <h1 className="font-bold text-md text-white">{label}</h1>

        <h1 className="text-md text-green-600">
          {Math.round(trip.co2Emission * 100) / 100}g CO2
        </h1>
      </div>
      <div className="w-3/4 bg-cff-charcoal text-white text-sm border-[1px] border-cff-anthracite rounded-b-md">
        <Timeline>
          <TimelineItem>
            <TimelineOppositeContent
              sx={{ m: "auto 0" }}
              align="right"
              variant="body2"
            >
              {new Date(trip.departure_time).toLocaleTimeString().slice(0, 5)}
            </TimelineOppositeContent>
            <TimelineSeparator>
              <TimelineConnector />
              <TimelineDot>
                <Home className="text-cff-charcoal" />
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent sx={{ m: "auto 0" }} align="left">
              <Typography>{trip.originName}</Typography>
            </TimelineContent>
          </TimelineItem>

          {trip.legs &&
            trip.legs.map((leg, index) => (
              <TimelineItem>
                <TimelineOppositeContent
                  sx={{ m: "auto 0" }}
                  align="right"
                  variant="body2"
                >
                  {new Date(leg.departure_time)
                    .toLocaleTimeString()
                    .slice(0, 5)}
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineConnector />
                  <TimelineDot>
                    <Commute className="" />
                  </TimelineDot>
                  <TimelineConnector />
                </TimelineSeparator>
                <TimelineContent sx={{ m: "auto 0" }} align="left">
                  <Typography>{leg.originName}</Typography>
                </TimelineContent>
              </TimelineItem>
            ))}

          <TimelineItem>
            <TimelineOppositeContent
              sx={{ m: "auto 0" }}
              align="right"
              variant="body2"
            >
              {new Date(trip.arrival_time).toLocaleTimeString().slice(0, 5)}
            </TimelineOppositeContent>
            <TimelineSeparator>
              <TimelineConnector />
              <TimelineDot>
                <FmdGood className="text-cff-red" />
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent sx={{ m: "auto 0" }} align="left">
              <Typography>{trip.destinationName}</Typography>
            </TimelineContent>
          </TimelineItem>
        </Timeline>
      </div>
    </div>
  );
}
