import { useRouter } from "next/navigation";
import Image from "next/image";

import { capitalizeFirstLetter } from "@/utils";
import Clip from "@/definitions";

type BookClipCardProps = {
	clip: Clip;
	clampContent: boolean;
	showMetadata?: boolean;
	showTitle?: boolean; // Title
	showAuthors?: boolean; // Authors only
	showDeleteButton?: boolean;
};

export default function BookClipCard({
	clip,
	clampContent = true,
	showMetadata = false,
	showTitle = false,
	showAuthors = false,
	showDeleteButton = false,
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
			return (
				<h2 title={clip.book.title} className=" text-sm line-clamp-1">
					{clip.book.title}
				</h2>
			);
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

	function handleDeleteClip() {
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/clip/" + clip.id;
		fetch(resourceUrl, {
			method: "DELETE",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		})
			.then((res) => {
				if (res.ok) {
					// Redirect to document page
					router.push("/document/" + clip.book.id);
				}
			})
			.catch((err) => {
				console.error("Could not delete clip:", err);
			});
	}

	function renderDeleteButton() {
		if (!showDeleteButton) return null;

		return (
			<button
				onClick={(e) => {
					e.stopPropagation();
					handleDeleteClip();
				}}
			>
				<div
					className="relative"
					style={{
						minWidth: 25,
						maxWidth: 25,
						minHeight: 25,
						maxHeight: 25,
					}}
				>
					<Image
						className="rounded-md object-cover bg-gray-200 hover:bg-orange-200 p-1"
						src="/trash.svg"
						alt="delete"
						fill={true}
						sizes="20vw"
					/>
				</div>
			</button>
		);
	}

	return (
		<div
			onClick={() => handleOnClick()}
			className="h-full w-full bg-white border border-border-300 hover:border-border-200 group relative flex cursor-pointer flex-col gap-1.5 rounded-xl py-5 px-6 transition-all ease-in-out hover:shadow-sm active:scale-[0.98] md:gap-4"
		>
			{renderTitle()}
			{renderAuthors()}
			{renderContent()}
			<div className="flex flex-row items-end justify-between gap-2">
				{renderMetadata()}
				{renderDeleteButton()}
			</div>
		</div>
	);
}
