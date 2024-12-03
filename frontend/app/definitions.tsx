export type Book = {
	id: string;
	title: string;
	authors: string[];
	createdAt: Date;
	updatedAt: Date | null;
	catalogueId: string | null;
	thumbnailUrl: string | null;
};

export type Clip = {
	id: string; // technically uuid v4
	book: Book;
	content: string;
	createdAt: Date;
	updatedAt: Date | null;
	locationType: string;
	clipStart: number | null;
	clipEnd: number | null;
};

export default Clip;
