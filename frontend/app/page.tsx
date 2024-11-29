import { getTimeOfDay } from "@/app/utils";

export default function Home() {
	const timeOfDay: string = getTimeOfDay();
	return (
		<div>
			<h1>Good {timeOfDay.charAt(0).toUpperCase() + timeOfDay.slice(1)}</h1>
		</div>
	);
}
