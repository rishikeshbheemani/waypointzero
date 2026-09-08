export interface DailyActivity {
  time: string;
  title: string;
  location: string;
  description: string;
  activity_type?: string | null;
  cost_estimate?: number | null;
}

export interface DailyPlan {
  day: number;
  theme?: string | null;
  day_summary?: string | null;
  activities: DailyActivity[];
}

export interface Itinerary {
  trip_title?: string | null;
  summary?: string | null;
  days: DailyPlan[];
}

export interface HotelRecommendation {
  name: string;
  neighborhood?: string | null;
  price_per_night_usd?: number | null;
  price_per_night?: number | null;
  rating?: number | null;
  category?: string | null;
  location_advantage?: string | null;
  amenities?: string[];
  description?: string | null;
}

export interface FlightOption {
  airline: string;
  route: string;
  estimated_price_usd?: number | null;
  notes?: string | null;
}

export interface TransitPassOption {
  name: string;
  coverage?: string | null;
  estimated_price?: number | null;
}

export interface TransportInfo {
  recommended_flights?: string[];
  local_transport?: string[];
  travel_passes?: string[];
  flight_options?: FlightOption[];
  transit_options?: Array<{ mode: string; route_or_system: string; estimated_cost?: number | null; description?: string }>;
  pass_options?: TransitPassOption[];
  tips?: string[];
}

export interface WeatherDay {
  date: string;
  weather_description?: string | null;
  temperature_max_celsius?: number | null;
  temperature_min_celsius?: number | null;
  precipitation_probability?: number | null;
}

export interface WeatherInfo {
  location?: string | null;
  forecast?: WeatherDay[];
  travel_impact?: string[];
  packing_recommendations?: string[];
}

export interface BudgetInfo {
  flights: number | string;
  accommodation: number | string;
  food: number | string;
  transportation: number | string;
  activities: number | string;
  total: number | string;
  remaining?: number | string | null;
  status: "within_budget" | "over_budget" | "flexible";
  currency: string;
  cost_saving_tips: string[];
}

export interface TripRequest {
  destination: string;
  origin?: string | null;
  duration_days: number;
  budget?: number | null;
  start_date?: string | null;
  interests?: string[];
  constraints?: string[];
}

export interface UserProfile {
  travel_style?: string | null;
  budget_tier?: string | null;
  preferred_airlines?: string[];
  walking_tolerance?: string | null;
  food_preferences?: string[];
}

export interface TripResponse {
  session_id: string;
  status: "completed" | "needs_clarification" | "error";
  clarification_question?: string | null;
  itinerary?: Itinerary | null;
  budget?: BudgetInfo | null;
  hotels: HotelRecommendation[];
  transport?: TransportInfo | null;
  weather?: WeatherInfo | null;
  research?: any;
}

export interface TripStatusResponse {
  session_id: string;
  destination?: string | null;
  duration_days?: number | null;
  has_itinerary: boolean;
  itinerary?: Itinerary | null;
  budget?: BudgetInfo | null;
  hotels: HotelRecommendation[];
  transport?: TransportInfo | null;
  weather?: WeatherInfo | null;
  research?: any;
}

export interface StreamEvent {
  event_type: "agent_start" | "agent_complete" | "clarification_needed" | "pipeline_complete" | "error";
  agent_name?: string | null;
  data: Record<string, any>;
  timestamp: string;
}
