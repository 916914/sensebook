// SPDX-License-Identifier: Apache-2.0
import { ButtonLink } from "@/components/button-link";
import { Container } from "@/components/container";

export default function NotFound() {
  return (
    <section aria-labelledby="nf-title" className="bg-night text-stone">
      <Container className="py-28 sm:py-36">
        <h1 id="nf-title" className="display display-l max-w-[16ch]">
          This page does not exist.
        </h1>
        <span aria-hidden="true" className="mt-10 block h-[2px] w-12 bg-marigold" />
        <p className="mt-10 max-w-md text-mist">The address may be mistyped, or the page may have moved. Everything on the site is reachable from the home page.</p>
        <div className="mt-10">
          <ButtonLink href="/">Go to the home page</ButtonLink>
        </div>
      </Container>
    </section>
  );
}
