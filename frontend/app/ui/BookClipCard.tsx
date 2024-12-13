import { useRouter } from "next/navigation";

import { capitalizeFirstLetter } from "@/utils";
import Clip from "@/definitions";

type BookClipCardProps = {
	clip: Clip;
	clampContent: boolean;
	showMetadata?: boolean;
	showTitle?: boolean; // Title
	showAuthors?: boolean; // Authors only
};

export default function BookClipCard({
	clip,
	clampContent = true,
	showMetadata = false,
	showTitle = false,
	showAuthors = false,
}: BookClipCardProps) {
	const router = useRouter();

	function handleOnClick() {
		// open the document
		console.log("Opening document", clip.id);
		router.push(`/clip/${clip.id}`);
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
			return <h2 className=" text-sm line-clamp-1">{clip.book.title}</h2>;
		}
	}
	function renderAuthors() {
		if (showAuthors) {
			return (
				<p className="text-xs font-thin italic line-clamp-1">
					{clip.book.authors.join(", ")}
				</p>
			);
		}
	}

	function renderMetadata() {
		// TODO
		if (showMetadata)
			return (
				<p className="italic text-sm text-slate-400">
					{capitalizeFirstLetter(clip.locationType)} {clip.clipStart}{" "}
					{clip.clipEnd ? `- ${clip.clipEnd}` : ""}
				</p>
			);
	}

	function renderContent() {
		if (!clampContent) {
			return <p className="text-md italic">{formatContent(clip.content)}</p>;
		}
		return (
			<p className="text-sm italic line-clamp-3">
				{formatContent(clip.content)}
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
