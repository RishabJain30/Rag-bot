package core;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentParser;
import dev.langchain4j.data.document.loader.FileSystemDocumentLoader;
import dev.langchain4j.data.document.parser.TextDocumentParser;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.data.document.splitter.DocumentByParagraphSplitter;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

public class FileIngestor {

    public List<TextSegment> ingest(String directoryPath) {
        List<TextSegment> allSegments = new ArrayList<>();

        System.out.println("Scanning directory: " + directoryPath);

        try (Stream<Path> paths = Files.walk(Paths.get(directoryPath))) {
            paths
                    .filter(Files::isRegularFile)
                    .forEach(file -> {
                        try {
                            DocumentParser parser = getParserForFile(file.toString());

                            if (parser != null) {
                                Document document = FileSystemDocumentLoader.loadDocument(file, parser);

                                DocumentByParagraphSplitter splitter = new DocumentByParagraphSplitter(500, 50);
                                List<TextSegment> chunks = splitter.split(document);

                                allSegments.addAll(chunks);
                                System.out.println("Ingested: " + file.getFileName() + " (" + chunks.size() + " chunks)");
                            }
                        } catch (Exception e) {
                            System.err.println("Failed to parse file: " + file.getFileName() + " - " + e.getMessage());
                        }
                    });
        } catch (Exception e) {
            System.err.println("Error reading directory: " + e.getMessage());
        }

        System.out.println("Total chunks generated: " + allSegments.size());
        return allSegments;
    }

    private DocumentParser getParserForFile(String filePath) {
        String lowerCasePath = filePath.toLowerCase();

        if (lowerCasePath.endsWith(".pdf")) {
            return new ApachePdfBoxDocumentParser();
        }
        else if (lowerCasePath.endsWith(".txt") ||
                lowerCasePath.endsWith(".java") ||
                lowerCasePath.endsWith(".py") ||
                lowerCasePath.endsWith(".md") ||
                lowerCasePath.endsWith(".json")) {
            return new TextDocumentParser();
        }

        return null;
    }

    public static void main(String[] args) {
        FileIngestor ingestor = new FileIngestor();
        String testPath = "C:/Users/Rishab/Desktop/Projects for CV/";
        ingestor.ingest(testPath);
    }
}