import BookDocument from "@/definitions";

type BookDocumentCardProps = BookDocument;

export default function BookDocumentCard(document: BookDocumentCardProps) {
	return (
		<div className="border border-border-300 hover:border-border-200 group relative flex cursor-pointer flex-col gap-1.5 rounded-xl py-3.5 pl-3.5 pr-1.5 transition-all ease-in-out hover:shadow-sm active:scale-[0.98] md:gap-2">
			<h2 className="line-clamp-1" >{document.title}</h2>
			<p className="text-sm italic line-clamp-2">{document.content} </p>
		</div>
	);
}
