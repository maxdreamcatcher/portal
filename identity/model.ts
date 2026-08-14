export function extractIdentity(req: Request, body: any) {
  // Minimal identity extraction used as a build-time stub.
  // Replace with your full identity logic.
  const headers = Object.fromEntries(req.headers as unknown as Iterable<[string, string]>);
  return {
    subject: (headers['x-subject'] as string) || headers['x-user'] || 'anonymous',
    headers,
  };
}
