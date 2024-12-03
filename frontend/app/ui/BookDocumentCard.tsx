import { useRouter } from "next/navigation";

import { capitalizeFirstLetter } from "@/utils";
import BookDocument from "@/definitions";

type BookDocumentCardProps = {
	document: BookDocument;
	clampContent: boolean;
	showMetadata?: boolean;
	showTitle?: boolean; // Title
	showAuthors?: boolean; // Authors only
};

export default function BookDocumentCard({
	document,
	clampContent = true,
	showMetadata = false,
	showTitle = false,
	showAuthors = false,
}: BookDocumentCardProps) {
	const router = useRouter();

	function handleOnClick() {
		// open the document
		console.log("Opening document", document.id);
		router.push(`/clip/${document.id}`);
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

	function renderTitle() {
		if (showTitle) {
			return <h2 className=" text-sm line-clamp-1">{document.title}</h2>;
		}
	}
	function renderAuthors() {
		if (showAuthors) {
			return (
				<p className="text-xs italic line-clamp-1">
					{document.authors.join(", ")}
				</p>
			);
		}
	}

	function renderMetadata() {
		// TODO
		if (showMetadata) return <></>;
	}

	function renderContent() {
		if (!clampContent) {
			return (
				<p className="text-sm italic">{formatContent(document.content)}</p>
			);
		}
		return (
			<p className="text-sm italic line-clamp-3">
				{formatContent(document.content)}
			</p>
		);
	}

	return (
		<div
			onClick={() => handleOnClick()}
			className="h-full w-full border border-border-300 hover:border-border-200 group relative flex cursor-pointer flex-col gap-1.5 rounded-xl py-5 px-6 transition-all ease-in-out hover:shadow-sm active:scale-[0.98] md:gap-4"
		>
			{renderTitle()}
			{renderAuthors()}
			{renderContent()}
			{renderMetadata()}
		</div>
	);
}
