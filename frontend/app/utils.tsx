export function getTimeOfDay(hours?: number): string {
	// For undeclared variables, typeof foo will return the string "undefined",
	// whereas the identity check foo === undefined would trigger the error
	// "foo is not defined".
	if (typeof hours === "undefined") {
		hours = new Date().getHours();
	}
	if (hours > 5 && hours < 12) {
		return "morning";
	} else if (hours >= 12 && hours < 18) {
		return "afternoon";
	} else {
		return "evening";
	}
}

export function capitalizeFirstLetter(val: string): string {
	return val.charAt(0).toUpperCase() + val.slice(1);
}
