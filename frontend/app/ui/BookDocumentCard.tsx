import BookDocument from "@/definitions";
import { capitalizeFirstLetter } from "@/utils";

type BookDocumentCardProps = BookDocument;

export default function BookDocumentCard(document: BookDocumentCardProps) {
	function formatContent(content: string): string {
		const charsToTrim = `"“'`;
		content = content.trim();
		if (charsToTrim.includes(content.charAt(0))) {
			content = content.slice(1);
		}
		// trim the end
		if (charsToTrim.includes(content.charAt(-1))) {
			content = content.slice(0, -1);
		}

		return capitalizeFirstLetter(content);
	}

	return (
		<div className="border border-border-300 hover:border-border-200 group relative flex cursor-pointer flex-col gap-1.5 rounded-xl py-3.5 pl-3.5 pr-1.5 transition-all ease-in-out hover:shadow-sm active:scale-[0.98] md:gap-2">
			<h2 className="line-clamp-1">{document.title}</h2>
			<p className="text-sm italic line-clamp-2">
				{formatContent(document.content)}
			</p>
		</div>
	);
}
