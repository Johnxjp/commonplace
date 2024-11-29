type BookDocument = {
	id: string; // technically uuid v4
	title: string;
	authors: string[];
	documentType: string;
	content: string;
	createdAt: Date;
	updatedAt: Date | null;
	isClip: boolean;
	clipStart: number | null;
	clipEnd: number | null;
	catalogueId: string;
};

export default BookDocument;
