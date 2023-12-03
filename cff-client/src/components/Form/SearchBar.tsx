import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Place } from "../../types/api_types";

interface SearchBarProps {
  placeholder: string;
  setValue: React.Dispatch<React.SetStateAction<Place>>;
}

interface RenderInputParams {
  InputLabelProps?: Record<string, unknown>;
  InputProps: Record<string, unknown>;
}

export default function SearchBar({ placeholder, setValue }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([] as Place[]);
  const visibleRef = useRef(false);

  useEffect(() => {
    if (query.trim() !== "" && visibleRef.current) {
      fetchSuggestions();
    } else {
      setSuggestions([]);
    }
    // Reset the userInteractionRef
    visibleRef.current = true;
  }, [query]);

  async function fetchSuggestions() {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_PLACE_API_URL}?name=${query}`
      );
      setSuggestions(response.data);
    } catch (error) {
      console.error("Error fetching suggestions:", error);
    }
  }

  function handleSuggestionClick(selectedValue: Place) {
    setQuery(selectedValue.name);
    setSuggestions([]);
    setValue(selectedValue);
    // Set the ref to true to indicate a user interaction
    visibleRef.current = false;
  }

  return (
    <div className="w-3/4 text-white">
      <div className="flex flex-col">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          autoComplete="off"
          className="rounded-md text-gray-100 p-2 bg-cff-charcoal border-[1px] border-cff-anthracite"
        />
      </div>

      <ul className="absolute bg-cff-charcoal rounded-md p-1">
        {suggestions.map((suggestion) => (
          <li
            key={suggestion.id}
            onClick={() => {
              handleSuggestionClick(suggestion);
            }}
          >
            {suggestion.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
