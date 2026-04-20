import axios from "axios";

const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: BASE,
  timeout: 10000
});

export const getSummary = async () => (await client.get("/metrics/summary")).data;
export const getTimeseries = async (hours = 24) => (await client.get(`/metrics/timeseries?hours=${hours}`)).data;
export const getModels = async () => (await client.get("/metrics/models")).data;
export const getCalls = async (limit = 50) => (await client.get(`/calls?limit=${limit}`)).data;
export const getAlerts = async () => (await client.get("/alerts")).data;
export const runSupportDemo = async () => (await client.post("/demo/run-support")).data;
