import BookDocument from "@/definitions";
import { capitalizeFirstLetter } from "@/utils";
import { useRouter } from "next/navigation";

type BookDocumentCardProps = BookDocument;

export default function BookDocumentCard(document: BookDocumentCardProps) {
	const router = useRouter();

	function handleOnClick() {
		// open the document
		router.push(`/annotation/${document.id}`);
	}

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
		<div
			onClick={() => handleOnClick()}
			className="h-full w-full border border-border-300 hover:border-border-200 group relative flex cursor-pointer flex-col gap-1.5 rounded-xl py-5 px-6 transition-all ease-in-out hover:shadow-sm active:scale-[0.98] md:gap-4"
		>
			<h2 className=" text-sm line-clamp-1">{document.title}</h2>
			<p className="text-sm italic line-clamp-3">
				{formatContent(document.content)}
			</p>
		</div>
	);
}
